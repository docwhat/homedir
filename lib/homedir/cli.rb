require 'thor'
require 'homedir'
require 'pathname'

module Homedir
  # The command line interface for {Homedir}.
  #
  # See the source or the command line tool `bin/homedir` for more
  # information
  class CLI < Thor
    attr_writer :repositories, :output

    no_tasks do
      # The directories to scan for repositories
      #
      # @return {Enumerable} A list of Pathname objects
      def repositories
        @repositories ||= [ Pathname.new(ENV['HOME']) + '.homedir' + 'packages']
      end

      # The stream to send output to.
      #
      # @return {IO}
      def output
        @output ||= $stdout
      end

      def puts *args
        output.puts *args
      end

      # Helper method to initialize the catalog, if needed.
      #
      # @return {Homedir::Catalog} A populated catalog
      def catalog
        @catalog ||= Catalog.new.tap do |cat|
          pdl = PackageDiscoveryLoader.new(cat)
          repositories.each do |repo|
            pdl.load_from_directory(repo)
          end
        end
      end

      # Helper method to display the info for a single package.
      #
      # @param {Homedir::Package} pkg The package to display info about
      def print_info(pkg)
        puts "Name:         #{pkg.name}"
        dependencies = if pkg.dependencies.length > 0
                         pkg.dependencies.sort.to_a.join(", ")
                       else
                         'none'
                       end
        puts "Dependencies: #{dependencies}"
        puts "Directory:    #{pkg.directory}"
        puts "Description:"
        pkg.description.split(/[\n\r]+/).each do |line|
          line = '' if line == "."
          puts "  #{line}"
        end
      end
    end

    desc "list", "Lists available packages."
    method_option(
      :remote,
      :type => :boolean,
      :default => false,
      :aliases => '-r',
      :description => "Queries the remote server")
    def list
      packages = catalog.sort.to_a
      puts "#{packages.length} local packages found:"
      packages.each do |package|
        puts " * #{package}"
      end
    end

    desc "info PACKAGE [PACKAGE...]", "Describe a specific PACKAGE in detail."
    def info(*package_name)
      package_name.each do |name|
        pkg = catalog.find_by_name(name)
        if pkg
          print_info pkg
        end
      end
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

    desc "repair", "Scans through your home directory and repairs all links. Warning: This can take a long time."
    def repair
      # FIXME: needs to do something
      puts "Not implemented yet"
    end
  end
end

