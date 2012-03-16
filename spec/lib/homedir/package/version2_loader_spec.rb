require 'spec_helper'
require 'pathname'
require 'homedir/package/version2_loader'

describe Homedir::PackageVersion2Loader do
  describe ".load_from_path" do
    context "with a version 2 package directory" do
      let(:package_path) { EXAMPLES_DIR + "version2-example" }
      let(:package) { subject.load_from_path package_path }

      it_behaves_like "a package loader"

      context "then the returned package should have" do

        it "the correct name" do
          package.name.should == "version2-example"
        end

        it "the correct description" do
          package.description.should == "This is an example version 2 package\nIt is showing off behavior that exists in version 2\n.\nThis description is basically meaningless."
        end

        it "the correct dependencies" do
          package.dependencies.should == Set.new(["version1-example", "version3-example"])
        end

        ['pre', 'post'].each do |prefix|
          ['install', 'remove'].each do |action|
            method_name = "#{prefix}_#{action}"
            it "the correct #{method_name}" do
              value = package.send(method_name)
              value.should_not be_nil
              value.should include("bin/bash")
            end
          end
        end
      end
    end
  end

end
