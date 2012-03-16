require 'homedir/package/loader'

module Homedir
  # This class is for loading collections of {Package packages}
  # from the file-system recursively.
  class PackageDiscoveryLoader
    attr_reader :catalog
    def initialize(catalog=nil)
      @catalog = catalog
    end

    # @private
    # @return [PackageLoader] A package loader instance
    def loader
      @loader ||= PackageLoader.new
    end

    # Recursively loads packages from the directory into {#catalog}
    #
    # @param {Pathname} path The directory to start scanning from
    # @return {Homedir::PackageDiscoveryLoader} self
    def load_from_directory path
      if loader.path_is_valid?(path)
        catalog << loader.load_from_path(path)
      else
        path.children.each do |child|
          load_from_directory(child) if child.directory?
        end
      end
      return self
    end
  end
end
