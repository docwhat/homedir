require 'spec_helper'
require 'pathname'
require 'homedir/package_version1_loader'

describe Homedir::PackageVersion1Loader do
  describe ".load_from_path" do
    context "with a version 1 package directory" do
      let(:package_path) { EXAMPLES_DIR + "version1-example" }
      let(:package) { subject.load_from_path package_path }

      it "returns a package" do
        package.should be_an_instance_of Homedir::Package
      end

      it "should be valid" do
        package.should be_valid
      end

      it "with the correct name" do
        package.name.should == "version1-example"
      end

      it "with the correct description" do
        package.description.should == "Some package description\n.\n...with multiple lines."
      end

      it "with the connect dependencies" do
        package.dependencies.should == Set.new(["version2-example", "version3-example"])
      end
    end
  end

  describe ".parse_control_file" do
    it "passes a stream to parse_control_stream" do
      path = Pathname.new __FILE__ # we don't care which file
      subject.stub(:parse_control_stream) { :success }
      subject.parse_control_file(path).should == :success
    end
  end

  describe ".parse_control_stream" do
    let(:path) { double(Pathname).as_null_object }

    context "with a control file" do
      let(:contents) {
        [
          "key: value",
          "multi: line1",
          "  line2",
          "complex:",
          "  line1 : is a colon",
          "  .",
          "  another : to confuse things",
        ]
      }
      let(:stream) { StringIO.new(contents.join "\n") }
      let(:hash) { subject.parse_control_stream stream }

      it "should understand key: value" do
        hash[:key].should == 'value'
      end

      it "should understand simple multilines" do
        hash[:multi].should == "line1\nline2"
      end

      it "should understand complex multilines" do
        hash[:complex].should == "line1 : is a colon\n.\nanother : to confuse things"
      end
    end
  end
end
