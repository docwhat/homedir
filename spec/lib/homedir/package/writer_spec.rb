require 'spec_helper'
require 'homedir/errors'
require 'homedir/package/writer'
require 'homedir/package/version3_loader'

describe Homedir::Package::Writer do
  describe ".write" do
    let(:pkg) { build :package }
    before(:each) do
      pkg.directory.dirname.mkdir
    end

    context "with a non-existant directory" do
      before(:each) { pkg.directory = Pathname.pwd + "a" + "b" }

      it "should raise an error" do
        expect {subject.write(pkg)}.to raise_error(Homedir::NoSuchDirectoryError)
      end
    end

    context "with the directory already existing" do
      before(:each) { FileUtils.mkdir_p pkg.directory.to_s }

      it "should raise an error" do
        expect {subject.write(pkg)}.to raise_error(Homedir::DuplicatePackageError)
      end
    end

    it "should have created the directory" do
      subject.write(pkg)
      pkg.directory.should be_a_directory
    end

    context "with the latest loader" do
      let(:loader) { Homedir::PackageVersion3Loader.new }
      before(:each) { subject.write(pkg) }

      it "should be detected as a valid version 3 package" do
        loader.should be_path_is_valid(pkg.directory)
      end

      it "should be valid" do
        loader.load_from_path(pkg.directory).should be_valid
      end

      it "should match the package we wrote" do
        newpkg = loader.load_from_path(pkg.directory)
        Homedir::Package::DEFAULT_VALUES.keys.each do |key|
          newpkg.send(key.to_sym).should == pkg.send(key.to_sym)
        end
      end
    end
  end
end
