require 'thor'

module Homedir
  class CLI < Thor

    desc "list", "List all known packages."
    method_option(
      :remote,
      :type => :boolean,
      :default => false,
      :aliases => '-r',
      :description => "Queries the remote server")
    def list
      # FIXME: list needs to do something
      puts "Not implemented yet"
    end

    desc "info PACKAGE", "Describe a specific PACKAGE in detail."
    def info(package_name)
      # FIXME: info needs to do something
      puts "Not implemented yet #{package_name.inspect}"
    end

    desc "enable PACKAGE...", "Enable PACKAGE, making it available in your home directory."
    def enable(*packages)
      # FIXME: info needs to do something
      puts "Not implemented yet #{packages.inspect}"
    end

    desc "disable PACKAGE...", "Disable PACKAGE, removing it from your home directory."
    def disable(*packages)
      # FIXME: info needs to do something
      puts "Not implemented yet #{packages.inspect}"
    end

    desc "create PACKAGE...", "Create PACKAGE, prompting you for information."
    method_option(
      :directory,
      :type => :string,
      :default => "#{ENV['HOME']}/.homedir/package",
      :aliases => "-d",
      :description => "Where to save the DIRECTORY."
    )
    def create(package_name)
      # FIXME: info needs to do something
      puts "Not implemented yet #{package_name.inspect}"
    end

  end
end

