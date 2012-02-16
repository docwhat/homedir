require 'homedir'
require 'pathname'
require 'fileutils'
require 'yaml'

module Homedir
  class Package
    # A package contains all the meta information about the package:
    #
    # * name, description, etc.
    # * pre and post install instructions.
    # * location of the package directory.
    #
    REQUIRED_OPTIONS = [
      :name,
      :description,
      :directory,
    ].freeze
    DEFAULT_OPTIONS = {
      :name         => nil,
      :description  => nil,
      :dependencies => [],
      :post_install => nil,
      :pre_install  => nil,
      :directory    => nil,
    }.freeze
    attr_accessor *DEFAULT_OPTIONS.keys


    def initialize(options = {})
      options = DEFAULT_OPTIONS.merge(options)

      # Set the options
      options.each do |k,v|
        send("#{k}=", v)
      end
    end

    def dependencies= value
      @dependencies = value.map { |p| p.to_s }
    end

    def directory= value
      @directory = value.nil? ? nil : Pathname.new(value)
    end

    def name= value
      raise "Invalid name: #{value.inspect}" unless value.nil? || value =~ /^[0-9a-zA-Z_-]+$/
      @name = value
    end

    def save!
      raise "The package is not valid: #{self}" unless valid?

      control_dir = directory + '.homedir'
      FileUtils.mkdir_p(control_dir.to_s) unless control_dir.directory?

      (control_dir + "control").open('w') do |f|
        f.write self.to_yaml
      end
    end

    def valid?
      REQUIRED_OPTIONS.reduce(true) do |is_valid, opt|
        is_valid && !instance_variable_get("@#{opt}").nil?
      end
    end

    def to_s
      @name
    end
  end
end
