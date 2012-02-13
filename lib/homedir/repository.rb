require 'pathname'
require 'homedir/package'

class Homedir::Repository
  attr_reader :directory, :package_loader, :packages, :name

  def initialize(directory, options={})
    options = {
      :package_loader => Homedir::Package,
    }.merge(options)
    @directory = Pathname.new(directory)
    @name = @directory.basename.to_s
    @package_loader = options[:package_loader]
  end

  def scan
    @packages = directory.each_child.map do |path|
      package_loader.load_directory path
    end.freeze
  end

end
