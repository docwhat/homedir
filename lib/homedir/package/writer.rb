require 'homedir/errors'

module Homedir
  class Package
    # This class is used to write out a package in
    # the latest format.
    class Writer

      # Write out the `package` to `directory`
      #
      # @param [Homedir::Package] package The package to write.
      def write(package)
        raise DuplicatePackageError if package.directory.exist?
        raise NoSuchDirectoryError unless package.directory.dirname.directory?
        dir = package.directory

        begin
          # Directory
          dir.mkdir

          # Contents directory
          (dir + 'homedir').mkdir

          # Control file
          (dir + 'homedir.yml').open('w') do |f|
            f.write({
              :name => package.name,
              :dependencies => package.dependencies,
            }.to_yaml)
          end

          # Description
          (dir + 'description.txt').open('w') do |f|
            f.write package.description
          end

          # Scripts
          Package::all_scripts.each do |script|
            contents = package.send script.to_sym
            unless contents.nil? || contents.to_s.strip == ''
              path = dir + "#{script}.sh"
              path.open('w') do |f|
                f.write contents
              end
              path.chmod(0744)
            end
          end
        rescue
          package.directory.rmtree
          raise
        end

      end
    end
  end
end
