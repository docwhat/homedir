require 'homedir/package'
require 'homedir/package_version1_loader'
require 'homedir/errors'

module Homedir
  # A class to load version 2 Package files from
  # a filesystem
  class PackageVersion2Loader < PackageVersion1Loader

    # Loads a package from a path
    #
    # @param {Pathname} path The directory of the package
    # @return {Homedir::Package} The package object
    def load_from_path(path)
      raise InvalidPackageDirectoryError.new("The directory '#{path}' is not a version 2 package.") unless path_is_valid?(path)
      control_path = path + '.homedir' + 'control'

      control = parse_control_file control_path

      pkg = Package.new( :directory => path )

      pkg.name = control[:package]
      pkg.description = control[:description] || ''
      pkg.dependencies = (control[:depends] || '').split("\n")

      ['pre', 'post'].each do |prefix|
        ['install', 'remove'].each do |action|
          filepath = (path + ".homedir" + "#{prefix}-#{action}")
          if filepath.file? and filepath.executable?
            filepath.open('r') do |f|
              pkg.send("#{prefix}_#{action}=", f.read())
            end
          end
        end
      end

      return pkg
    end

    # Is the path a valid version2 package directory?
    #
    # @return {Boolean} Returns true if the path is a valid package directory.
    def path_is_valid? path
      return false unless (path).directory?
      return false unless (path + '.homedir').directory?
      return false unless (path + '.homedir' + 'control').file?
      return true
    end
  end
end
