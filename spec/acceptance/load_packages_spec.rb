require 'spec_helper'
require 'homedir'

TEST_DIR = Pathname.new("load_packages")

def mkv1pkg(name, dependencies=[])
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

def mkv2pkg(name, dependencies=[])
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

def mkv3pkg(name, dependencies=[])
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

describe "Loading packages" do
  context "with a fake set of packages" do
    before(:each) do
      mkv1pkg("version1")
      mkv2pkg("version2")
      mkv3pkg("version3")
    end

    it "can read all packages" do
      pending "Work In Progress"
      catalog = Homedir::Catalog.new
      catalog.load(TEST_DIR)
      catalog.length.should == 3
      names = catalog.map { |p| p.name }
      names.should include("version1")
      names.should include("version2")
      names.should include("version3")
    end

  end
end
