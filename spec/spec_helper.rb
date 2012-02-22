require 'homedir/hacks'
require 'fileutils'
require 'tmpdir'
require 'factory_girl'
require 'factories'

TEST_DIR = Pathname.new("load_packages")

RSpec.configure do |config|
  # Allows using build(), create(), etc. without the "FactoryGirl." part.
  config.include FactoryGirl::Syntax::Methods

  config.before(:each) do
    @directory = Dir.mktmpdir('homedir-spec-')
    @orig_directory = Dir.pwd
    Dir.chdir(@directory)
  end

  config.after(:each) do
    Dir.chdir(@orig_directory)
    FileUtils.rmtree(@directory)
  end
end

def make_package_v1(name, dependencies=[])
  root_path = TEST_DIR + name
  root_path.mkdir_p
  control = root_path + ".homedir.control"
  control.open('w') do |f|
    f.puts "package: #{name}"
    f.puts "priority: normal"
    f.puts "maintainer: Christian Holtje <docwhat@gerf.org>"
    if dependencies.length > 0
      f.print "depends:"
      dependencies.each { |dep| f.puts "  #{dep}" }
    end
    f.puts "standards-version: 1"
    f.puts "description:"
    f.puts "  Some package description"
    f.puts "  ."
    f.puts "  ...with multiple lines."
  end
end

def make_package_v2(name, dependencies=[])
  root_path = TEST_DIR + name
  root_path.mkdir_p
  homedir_path = TEST_DIR + '.homedir'
  homedir_path.mkdir_p
  control = homedir_path + "control"
  control.open('w') do |f|
    f.puts "package: #{name}"
    f.puts "priority: normal"
    f.puts "maintainer: Christian Holtje <docwhat@gerf.org>"
    if dependencies.length > 0
      f.print "depends:"
      dependencies.each { |dep| f.puts "  #{dep}" }
    end
    f.puts "standards-version: 1"
    f.puts "description:"
    f.puts "  Some package description"
    f.puts "  ."
    f.puts "  ...with multiple lines."
  end

  ['pre','post'].each do |prefix|
    ['install', 'remove'].each do |suffix|
      path = homedir_path + "#{prefix}-#{suffix}"
      path.open('w') do |f|
        f.puts "echo #{prefix}-#{suffix}"
      end
    end
  end
end

def make_package_v3(name, dependencies=[])
  root_path = TEST_DIR + name
  root_path.mkdir_p
  homedir_path = TEST_DIR + '.homedir'
  homedir_path.mkdir_p
  control = homedir_path + "control"
  control.open('w') do |f|
    f.puts "name: #{name}"
    f.puts "description: ! 'a really long description"
    f.puts "  that goes for multiple lines"
    f.puts "  etc."
    f.puts
    f.puts "  the end'"
    f.puts "dependencies:"
    dependencies.each do |dep|
      fputs "- #{dep}"
    end
  end

  ['pre','post'].each do |prefix|
    ['install', 'remove', 'update'].each do |suffix|
      path = homedir_path + "#{prefix}-#{suffix}"
      path.open('w') do |f|
        f.puts "echo #{prefix}-#{suffix}"
      end
    end
  end
end
