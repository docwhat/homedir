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
      pkg = Package.new(:directory => path)
      control_file = path + 'homedir.yml'
      raise InvalidPackageDirectoryError.new("The directory #{path} isn't a valid package") unless control_file.file?
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
  end
end
