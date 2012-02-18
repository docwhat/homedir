require 'homedir/errors'

module Homedir
  class Catalog < Set

    # @param {String} name The name of the {Homedir::Package package} to find.
    # @return {Homedir::Package} The package that matches the `name`
    def find_by_name name
      found = select { |pkg| pkg.name == name }
      raise "Invalid package object(s): #{found.inspect}" unless found.length <= 1
      found.first
    end

    # Returns all dependencies for `package` including `package` itself.
    #
    # @raise [Homedir::MissingDependendency] if a dependency cannot be found.
    # @param {Homedir::Package} package The package to get dependencies for.
    # @return {Set} The {Homedir::Package Package} objects that `package` depends on.
    def find_all_dependencies package
      found = Set.new([package])
      find_all_dependencies_not_found found, package
      return found
    end

    private

    # This is the method that does the work for {#find_all_dependencies}.
    #
    # @param {Set} found The set of all found packages.
    # @param {Homedir::Package} package The package to get dependencies for. It is assumed it is already in `found`
    def find_all_dependencies_not_found found, package
      package.dependencies.each do |dependency_name|
        dependency = find_by_name dependency_name

        raise MissingDependencyError.new(
          "The package '#{package}' requires '#{dependency_name}' which cannot be found."
        ) if dependency.nil?

        if not found.include? dependency
          found << dependency
          find_all_dependencies_not_found(found, dependency)
        end
      end
      return nil
    end
  end
end
