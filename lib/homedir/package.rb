require 'homedir/errors'
require 'pathname'
require 'fileutils'
require 'yaml'

# A package contains all the meta information about the package:
#
# * name, description, etc.
# * pre and post install instructions.
# * location of the package directory.
#
module Homedir
  class Package
    # A list of required values. If a value in this
    # list isn't set, then the object isn't {#valid? valid}.
    # @see #valid?
    REQUIRED_VALUES = [
      :name,
      :description,
      :directory,
    ].freeze
    DEFAULT_VALUES = {
      :name         => nil,
      :description  => nil,
      :dependencies => [],
      :pre_install  => nil,
      :post_install => nil,
      :pre_remove   => nil,
      :post_remove  => nil,
      :pre_update   => nil,
      :post_update  => nil,
      :directory    => nil,
    }.freeze

    # The name of the package.
    #
    # * It must match the regex: `[a-zA-Z0-9_-]`.
    # * It must match the directory it'll be written-to/read-from
    #
    # @return {String} The name of the package
    attr_reader :name

    # A description of the package for humans.
    #
    # @return {String} The description of the package
    attr_accessor :description

    # A list of package names this package depends on.
    #
    # When assigning a list, they can either be {Homedir::Package Package} objects or strings.
    # @return [Set] The set of package {#name names}.
    attr_reader :dependencies

    # A script to run before a package is enabled.
    #
    # @return {String}
    attr_accessor :pre_install

    # A script to run after a package is enabled.
    #
    # @return {String}
    attr_accessor :post_install

    # A script to run before the package is disabled.
    # @return {String}
    attr_accessor :pre_remove

    # A script to run after the package is disabled
    # @return {String}
    attr_accessor :post_remove

    # A script to run before upgrading the package's source
    #
    # This is run before any upgrade steps run for the package source.
    # @return {String}
    attr_accessor :pre_update

    # A script that runs after upgrading the package's source
    #
    # This is run after a package is upgraded and after the
    # the package has been re-enabled but before the pre_install
    # script.
    # @return {String}
    attr_accessor :post_update

    # The directory where the package is stored.
    #
    # * The directory's basename must match {#name}.
    #
    # @return {Pathname}
    attr_reader :directory

    # Create a new {Package} instance.
    #
    # @param {Hash} options
    # @option options {String} :name The name of the package.
    # @option options {String} :description The description of the package.
    # @option options {Enumerable} :dependencies A list of {Homedir::Package packages} or {String strings}.
    # @option options {Pathname} :directory The directory the packages is located at.
    # @option options {String} :post_install Commands to run after installing the package.
    # @option options {String} :pre_uninstall Commands to run before uninstalling the package.
    def initialize(options = {})
      options = DEFAULT_VALUES.merge(options)

      # Set the options
      options.each do |k,v|
        send("#{k}=", v)
      end
    end

    # The hashes are based on the name
    # @return {Fixnum} The hash
    def hash
      @name.hash
    end

    # Returns true if the packages have the same name.
    #
    # @param {Homedir::Package} other The package to check for equality to.
    # @return {Boolean} `true` if the `name` matches.
    def eql?(other)
      if other.respond_to? :name
        other.name == @name
      else
        false
      end
    end

    # Comparison method used for sorting.
    #
    # Note: `list_of_packages.sort_by{|p| p.name}` is much faster.
    #
    # @return {FixNumber} -1, 0, or 1 if other is less, equal, greater than self
    def <=>(other)
      self.name <=> other.name
    end

    # {include:#dependencies}
    def dependencies= value
      @dependencies = Set.new( value.map { |p| p.to_s } )
    end

    # {include:#directory}
    def directory= value
      @directory = value.nil? ? nil : Pathname.new(value)
    end

    # {include:#name}
    # @param {String} value The new name for the package.
    # @raise [Homedir::InvalidNameError] If the name doesn't match the regexp `/^[0-9a-zA-Z_-]+$/`
    def name= value
      raise InvalidNameError.new(
        "The name #{value.inspect} must only contain numbers, letters, `_` and `-`"
      ) unless value.nil? || value =~ /^[0-9a-zA-Z_-]+$/
      @name = value
    end

    # Saves the package info to {#directory}`/.homedir/` if it {#valid? valid}.
    #
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
    #
    # @return {Boolean} `true` if the package is valid.
    def valid?
      errors = []
      REQUIRED_VALUES.each do |value|
        errors << "#{value} must not be empty." if instance_variable_get("@#{value}").nil?
      end
      # FIXME: This should check that .directory.basename == .name
      @errors = errors
      @errors.length == 0
    end

    # A list of errors
    #
    # This list is only filled after {#.valid?} is run.
    # @return [Array] An array of strings describing the problems.
    def errors
      @errors || []
    end

    # Returns the {#name} attribute
    #
    # @return {String} The {#name} of the package.
    def to_s
      @name
    end

  end
end
