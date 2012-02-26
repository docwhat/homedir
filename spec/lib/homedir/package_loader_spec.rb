require 'spec_helper'
require 'homedir/package'
require 'homedir/package_loader'

describe Homedir::PackageLoader do
  EXAMPLES_DIR.children.each do |path|
    context "with the example package '#{path.basename}'" do
      let(:package_path) { path }
      let(:package) { subject.load_from_path package_path }

      it_behaves_like "a package loader"
    end
  end

  context "with a missing package directory" do
    let(:path) { Pathname.new "doesnt-exist" }
    it "should raise an exception" do
      expect { subject.load_from_path path }.to raise_error(Homedir::InvalidPackageDirectoryError)
    end
  end

  context "with an invalid package directory" do
    let(:path) { Pathname.new "invalid-package" }
    before(:each) { path.mkdir }
    it "should raise an exception" do
      expect { subject.load_from_path path }.to raise_error(Homedir::InvalidPackageDirectoryError)
    end
  end

end
