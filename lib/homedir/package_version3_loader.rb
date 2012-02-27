require "yaml"
require "homedir/package"
require "homedir/errors"

module Homedir
  class PackageVersion3Loader
    # Loads a package from a path
    #
    # @param {Pathname} path The directory of the package
    # @return {Homedir::Package} The package object
    def load_from_path(path)
      raise InvalidPackageDirectoryError.new("The directory '#{path}' isn't a valid version 3 package") unless path_is_valid?(path)
      pkg = Package.new(:directory => path)
      control_file = path + 'homedir.yml'
      control = YAML::load_file control_file.to_s
      pkg.description = (path + 'description.txt').read()
      pkg.name = control[:name]
      pkg.dependencies = control[:dependencies]

      ['pre', 'post'].each do |prefix|
        ['install', 'remove', 'update'].each do |action|
          filepath = (path + "#{prefix}-#{action}.sh")
          if filepath.file? and filepath.executable?
            filepath.open('r') do |f|
              pkg.send("#{prefix}_#{action}=", f.read())
            end
          end
        end
      end

      return pkg
    end

    # Is the path a valid version3 package directory?
    #
    # @return {Boolean} Returns true if the path is a valid package directory.
    def path_is_valid? path
      return false unless (path).directory?
      return false unless (path + 'homedir.yml').file?
      return false unless (path + 'description.txt').file?
      return false unless (path + 'homedir').directory?
      return true
    end
  end
end
