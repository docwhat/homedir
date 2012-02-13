require 'spec_helper'
require 'homedir/package'
require 'pathname'

describe Homedir::Package do

  context "loading a v3 package from disk" do
    describe "#read_from_directory"
  end

  describe "#new" do
    context "creating a package from scratch" do
      describe "dependencies" do
        it "should accept all strings" do
          package = build(:package, :dependencies => ['another_package'])
          package.dependencies.size.should == 1
          package.dependencies[0].should == 'another_package'
        end
        it "should accept packages" do
          another_package = build(:package)
          package = build(:package, :dependencies => [another_package])
          package.dependencies.size.should == 1
          package.dependencies[0].should == another_package.name
        end
      end

      it "should set .name" do
        name = "a-name"
        build(:package, :name => name).name.should == name
      end

      it "should set .description" do
        desc = "some words"
        build(:package, :description => desc).description.should == desc
      end
    end
  end

  describe "#from_directory" do
    it "should read its configuration from a directory"
  end

  describe ".name" do
    it "should not accept an invalid name" do
      pkg = build(:package)
      expect { pkg.name = "a name" }.to raise_error
    end
  end

  describe ".valid?" do
    it "should require a name" do
      build(:package, :name => nil).should_not be_valid
    end

    it "should require a description" do
      build(:package, :description => nil).should_not be_valid
    end
  end

  describe ".directory" do
    it "should be a Pathname object" do
      build(:package).directory.should be_an_instance_of(Pathname)
    end
  end

  describe ".save!" do
    it "should refuse to save if invalid" do
      pkg = build(:package, :name => nil)
      expect { pkg.save! }.to raise_error
    end

    it "should refuse to save if directory isn't set" do
      pkg = build(:package, :directory => nil)
      expect { pkg.save! }.to raise_error
    end

    it "should save files to '.homedir'" do
      pkg = create(:package)
      dot_homedir = Pathname.new(pkg.directory) + '.homedir'
      dot_homedir.should be_a_directory
    end
  end
end
