require 'spec_helper'
require 'homedir/cli'
require 'tmpdir'

describe Homedir::CLI do
  before(:each) do
    subject.repositories = [ EXAMPLES_DIR ]
  end

  context "list" do
    let(:output) { capture(:stdout) { subject.list } }

    it "returns a list" do
      output.should include(" * version1-example")
      output.should include(" * version2-example")
    end
  end

  context "info PACKAGE" do
    let(:output) { capture(:stdout) { subject.info "version3-example" } }

    it "displays the package name" do
      output.should =~ /^Name:\s+version3-example$/
    end

    it "displays the dependencies" do
      output.should =~ /^Dependencies:\s+/
    end

    it "displays the directory" do
      output.should =~ /^Directory:\s+#{EXAMPLES_DIR}/
    end

    it "displays the description" do
      output.should =~ /Description:\s+/
    end
  end

  context "info PACKAGE PACKAGE" do
    let(:output) { capture(:stdout) { subject.info "version3-example", "version2-example" } }

    it "displays both package names" do
      output.should =~ /^Name:\s+version3-example$/
      output.should =~ /^Name:\s+version2-example$/
    end
  end

  context "enable PACKAGE" do
    pending "Not implemented yet"
  end

  context "disable PACKAGE" do
    pending "Not implemented yet"
  end

  context "create PACKAGE" do
    let(:dir) { Pathname.pwd }
    before(:each) do
      subject.options = {"directory" =>  dir.to_s}
    end

    context "with --directory" do
      it "should create the directory" do
        silence(:stdout) { subject.create('foopkg') }
        (dir + 'foopkg').should be_directory
      end

      it "should the directory should contain a valid package" do
        silence(:stdout) { subject.create('foopkg') }
        pkg = Homedir::PackageLoader.new.load_from_path(dir + 'foopkg')
        pkg.name.should == 'foopkg'
      end

      it "should print info about the package" do
        subject.should_receive(:print_info)
        silence(:stdout) { subject.create('foopkg') }
      end

    end

    context "with a non-existant --directory" do
      let(:dir) { Pathname.pwd + "somedirectory" + "thatdoesnot" + "exist" }

      it "should print an error message" do
        subject.stub(:exit)
        subject.should_receive(:error)
        silence(:stderr) { subject.create('foopkg') }
      end

    end
    context "with already existant --directory" do
      let(:dir) { Pathname.pwd }
      let(:name) { "foopkg" }
      before(:each) do
        (dir + name).mkdir
        subject.stub(:exit)
      end

      it "should print an error message" do
        subject.should_receive(:error)
        silence(:stderr) { subject.create(name) }
      end

    end
  end

  context "repair" do
    pending "Not implented yet"
  end
end
