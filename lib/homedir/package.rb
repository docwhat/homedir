require 'homedir'
require 'pathname'
require 'fileutils'
require 'yaml'

# A package contains all the meta information about the package:
#
# * name, description, etc.
# * pre and post install instructions.
# * location of the package directory.
#
class Homedir::Package
  # A list of required values. If a value in this
  # list isn't set, then the object isn't {#valid? valid}.
  # @see #valid?
  REQUIRED_VALUES = [
    :name,
    :description,
    :directory,
  ].freeze
  DEFAULT_VALUES = {
    :name           => nil,
    :description    => nil,
    :dependencies   => [],
    :post_install   => nil,
    :pre_uninstall  => nil,
    :directory      => nil,
  }.freeze

  # The name of the package.
  #
  # * It must match the regex: `[a-zA-Z0-9_-]`.
  # * It must match the directory it'll be written-to/read-from
  attr_reader :name

  # A description of the package for humans.
  attr_accessor :description

  # A list of package names this package depends on.
  #
  # @param [Enumerable] value A list of packages. They can be either {Homedir::Package Package} objects or strings.
  attr_reader :dependencies

  # A script that should run after install.
  attr_accessor :post_install

  # A script to run before install.
  attr_accessor :pre_uninstall

  # The directory where the package is stored.
  #
  # * The directory's basename must match {#name}.
  attr_reader :directory

  def initialize(options = {})
    options = DEFAULT_VALUES.merge(options)

    # Set the options
    options.each do |k,v|
      send("#{k}=", v)
    end
  end

  # {include:#dependencies}
  def dependencies= value
    @dependencies = value.map { |p| p.to_s }
  end

  # {include:#directory}
  def directory= value
    @directory = value.nil? ? nil : Pathname.new(value)
  end

  # {include:#name}
  def name= value
    raise "Invalid name: #{value.inspect}" unless value.nil? || value =~ /^[0-9a-zA-Z_-]+$/
    @name = value
  end

  # Saves the package info to {#directory}`/.homedir/` if it {#valid? valid}.
  # @see #valid?
  def save!
    raise "The package is not valid: #{self}" unless valid?

    control_dir = directory + '.homedir'
    FileUtils.mkdir_p(control_dir.to_s) unless control_dir.directory?

    (control_dir + "control").open('w') do |f|
      f.write self.to_yaml
    end
  end

  # Verifies the package is valid to save.
  def valid?
    # FIXME: This should check that .directory.basename == .name
    REQUIRED_VALUES.reduce(true) do |is_valid, opt|
      is_valid && !instance_variable_get("@#{opt}").nil?
    end
  end

  def to_s
    @name
  end
end
