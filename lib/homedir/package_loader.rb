require 'homedir/errors'
require 'homedir/package_version1_loader'
require 'homedir/package_version2_loader'
require 'homedir/package_version3_loader'

module Homedir
  class PackageLoader

    # The list of loaders, in the order they should be tried
    #
    # @return {Enumerable} A list of package loaders
    def loaders
      # The order is important
      @loaders ||= [
        PackageVersion3Loader.new,
        PackageVersion2Loader.new,
        PackageVersion1Loader.new,
      ].freeze
    end

    def load_from_path path
      loaders.each do |loader|
        begin
          return loader.load_from_path(path)
        rescue InvalidPackageDirectoryError
          next
        end
      end

      raise InvalidPackageDirectoryError.new("The directory '#{path}' doesn't contain a valid package")
    end

  end
end
