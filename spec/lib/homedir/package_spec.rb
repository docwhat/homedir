require 'spec_helper'
require 'homedir/package'
require 'homedir/hacks'
require 'homedir/errors'
require 'pathname'

shared_examples "a string setter and getter" do
  let(:attribute) { :setter }
  it "should be setable" do
    subject.send("#{attribute}=", "some string")
  end
  it "should be getable" do
    subject.send("#{attribute}=", "some string")
    subject.send(attribute).should == "some string"
  end
  it "should be set to nil" do
    subject.send("#{attribute}=", nil)
    subject.send(attribute).should == nil
  end
end

describe Homedir::Package do

  describe "#new" do
    context "creating a package from scratch" do
      describe "dependencies" do
        it "should accept all strings" do
          package = build(:package, :dependencies => ['another_package'])
          package.dependencies.should == Set.new(['another_package'])
        end
        it "should accept packages" do
          another_package = build(:package)
          package = build(:package, :dependencies => [another_package])
          package.dependencies.should == Set.new([another_package.name])
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

  describe ".hash" do
    it "should be the same for two identically named packages" do
      pkg1 = build(:package, :name => 'samename')
      pkg2 = build(:package, :name => pkg1.name)
      pkg1.hash.should == pkg2.hash
    end
  end

  describe ".eql?" do
    it "should be true for identically named packages" do
      pkg1 = build(:package, :name => 'samename')
      pkg2 = build(:package, :name => pkg1.name)
      pkg1.should eql(pkg2)
    end
  end

  describe ".name" do
    it "cannot have spaces" do
      pkg = build(:package)
      expect { pkg.name = "a name" }.to raise_error(Homedir::InvalidNameError)
    end
  end

  describe ".pre_install" do
    it_behaves_like "a string setter and getter" do
      let(:attribute) { :pre_install }
    end
  end
  describe ".post_install" do
    it_behaves_like "a string setter and getter" do
      let(:attribute) { :post_install }
    end
  end
  describe ".pre_remove" do
    it_behaves_like "a string setter and getter" do
      let(:attribute) { :pre_remove }
    end
  end
  describe ".post_remove" do
    it_behaves_like "a string setter and getter" do
      let(:attribute) { :post_remove }
    end
  end
  describe ".pre_update" do
    it_behaves_like "a string setter and getter" do
      let(:attribute) { :pre_update }
    end
  end
  describe ".pre_update" do
    it_behaves_like "a string setter and getter" do
      let(:attribute) { :post_update }
    end
  end

  describe ".valid?" do
    context "name" do
      it "is required" do
        build(:package, :name => nil).should_not be_valid
      end

      it "should be shown in .errors" do
        pkg = build(:package, :name => nil)
        pkg.valid?
        pkg.errors.join.should include("name must not be empty")
      end
    end

    context "description" do
      it "should require a description" do
        build(:package, :description => nil).should_not be_valid
      end

      it "should be shown in .errors" do
        pkg = build(:package, :description=> nil)
        pkg.valid?
        pkg.errors.join.should include("description must not be empty")
      end
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
