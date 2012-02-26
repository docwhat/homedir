require 'spec_helper'
require 'pathname'
require 'homedir/package_version3_loader'

describe Homedir::PackageVersion3Loader do
  describe ".load_from_path" do
    context "with a version 3 package directory" do
      let(:package_path) { EXAMPLES_DIR + "version3-example" }
      let(:package) { subject.load_from_path package_path }

      it_behaves_like "a package loader"

      context "then the returned package should have" do

        it "the correct name" do
          package.name.should == "version3-example"
        end

        it "the correct description" do
          package.description.should == "This describes a version 3 package.\n\nThe user can put whatever text in here they want and it'll be shown to the user.\n"
        end

        it "the correct dependencies" do
          package.dependencies.should == Set.new(["version1-example", "version2-example"])
        end

        ['pre', 'post'].each do |prefix|
          ['install', 'remove', 'update'].each do |action|
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
