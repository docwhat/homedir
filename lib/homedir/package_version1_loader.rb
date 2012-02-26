require 'homedir/package'
require 'homedir/errors'

module Homedir
  class PackageVersion1Loader
    def initialize(package_class=Homedir::Package)
      @package_class = package_class
    end

    # Loads a package from a path
    #
    # @param {Pathname} path The directory of the package
    # @return {Homedir::Package} The package object
    def load_from_path(path)
      control_path = path + '.homedir.control'
      raise InvalidPackageDirectoryError.new("The directory '#{path}' is not a version 1 package.") unless control_path.file?

      control = parse_control_file control_path

      pkg = @package_class.new( :directory => path )

      pkg.name = control[:package]
      pkg.description = control[:description] || ''
      pkg.dependencies = (control[:depends] || '').split("\n")

      return pkg
    end

    # Parse a control file
    #
    # @param {Pathname} path The path to control file
    # @return {Hash} A hash containing the keys/values.
    # @see {#parse_control_stream}
    def parse_control_file path
      path.open('r') { |f| parse_control_stream f }
    end

    # Parse a version 1 control from a stream
    #
    # This is *not* a robust parser.
    # @param {IO} stream An IO stream to read from
    # @return {Hash} A hash containing the keys/values.
    def parse_control_stream stream
      contents = stream.read()

      hash = {}
      last_key = nil
      last_value = nil
      contents.split(/[\r\n]+/).each do |line|
        next if line =~ /^\s*#/
        if line =~ /^\s/
          last_value << line.strip unless last_key.nil?
        elsif line.include? ":"
          hash[last_key.to_sym] = last_value.join("\n") unless last_key.nil?
          last_key, value = line.split(/\s*:\s*/, 2)
          last_value = value.strip.empty? ? [] : [ value.strip ]
        end
      end
      hash[last_key.to_sym] = last_value.join("\n") unless last_key.nil?

      return hash
    end
  end
end
