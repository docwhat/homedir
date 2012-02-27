require 'homedir/errors'

shared_examples "a package loader" do
  describe ".load_from_path" do
    context "with a package directory" do

      it "returns a package" do
        package.should be_an_instance_of Homedir::Package
      end

      it "should be valid" do
        package.should be_valid
      end
    end

    context "with a missing package directory" do
      let(:package_path) { Pathname.new "does-not-exist" }

      it "raises an exception" do
        expect { package }.to raise_error(Homedir::InvalidPackageDirectoryError)
      end
    end

    context "with an invalid package directory" do
      let(:package_path) { Pathname.new "exists" }
      before(:each) { package_path.mkdir }

      it "raises an exception" do
        expect { package }.to raise_error(Homedir::InvalidPackageDirectoryError)
      end
    end
  end

  describe ".path_is_valid?" do
    context "with a package directory" do

      it "returns true" do
        subject.should be_path_is_valid(package_path)
      end
    end

    context "with a missing package directory" do
      let(:package_path) { Pathname.new "does-not-exist" }

      it "returns false" do
        subject.should_not be_path_is_valid(package_path)
      end
    end

    context "with an invalid package directory" do
      let(:package_path) { Pathname.new "exists" }
      before(:each) { package_path.mkdir }

      it "returns false" do
        subject.should_not be_path_is_valid(package_path)
      end
    end
  end
end
