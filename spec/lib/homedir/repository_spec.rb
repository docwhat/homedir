require 'spec_helper'
require 'homedir/repository'
require 'pathname'

describe Homedir::Repository do
  subject { Homedir::Repository.new directory, :package_loader => package_loader }
  let(:package_loader) do
    double().tap do |pl|
      # :package is a placeholder for a Package instance
      pl.stub(:load_directory) { :package }
    end
  end
  let(:directory) { Pathname.new('/') } # an absolute directory
  let(:package_dirs) { (1..10).map { |n| directory + "package-#{n}" } }

  before(:each) do
    # We need to make the directories exist so it can be scaned
    package_dirs.each { |p| p.mkdir }
  end

  describe "#new" do
    subject { Homedir::Repository }

    it "should take a directory name" do
      subject.new directory.to_s
    end

    it "should accept a pathname object" do
      subject.new directory
    end

    it "should accept a Package class" do
      subject.new directory, :package_loader => double()
    end
  end

  describe ".scan" do
    it "should load each package" do
      package_dirs.each do |p|
        package_loader.should_receive(:load_directory).with(p)
      end
      subject.scan.size.should == package_dirs.size
    end
  end

  describe ".packages" do
    it "should contain package objects" do
      subject.scan
      subject.packages.each do |p|
        p.should == :package
      end
    end
  end

  describe ".name" do
    it "should return the basename of the directory" do
      repo = Homedir::Repository.new Pathname.new('/a/b/my-name')
      repo.name.should == 'my-name'
    end
  end

end
