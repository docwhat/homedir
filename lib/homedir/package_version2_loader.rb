require 'homedir/package'
require 'homedir/package_version1_loader'
require 'homedir/errors'

module Homedir
  class PackageVersion2Loader < PackageVersion1Loader

    # Loads a package from a path
    #
    # @param {Pathname} path The directory of the package
    # @return {Homedir::Package} The package object
    def load_from_path(path)
      control_path = path + '.homedir' + 'control'
      raise InvalidPackageDirectoryError.new("The directory '#{path}' is not a version 2 package.") unless control_path.file?

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

  end
end
