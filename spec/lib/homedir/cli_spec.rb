require 'spec_helper'
require 'homedir/cli'
require 'tmpdir'

describe Homedir::CLI do
  before(:each) do
    subject.repositories = [ EXAMPLES_DIR ]
    subject.output = output
  end
  let(:output) { StringIO.new }

  context "list" do
    before(:each) { subject.list }

    it "returns a list" do
      output.string.should include(" * version1-example")
      output.string.should include(" * version2-example")
    end
  end

  context "info PACKAGE" do
    before(:each) { subject.info "version3-example" }

    it "displays the package name" do
      output.string.should =~ /^Name:\s+version3-example$/
    end

    it "displays the dependencies" do
      output.string.should =~ /^Dependencies:\s+/
    end

    it "displays the directory" do
      output.string.should =~ /^Directory:\s+#{EXAMPLES_DIR}/
    end

    it "displays the description" do
      output.string.should =~ /Description:\s+/
    end
  end

  context "info PACKAGE PACKAGE" do
    before(:each) { subject.info "version3-example", "version2-example" }

    it "displays both package names" do
      output.string.should =~ /^Name:\s+version3-example$/
      output.string.should =~ /^Name:\s+version2-example$/
    end
  end

  context "enable PACKAGE" do
    pending "Not implemented yet"
  end

  context "disable PACKAGE" do
    pending "Not implemented yet"
  end

  context "create PACKAGE" do
    pending "Not implented yet"
  end

  context "repair" do
    pending "Not implented yet"
  end
end
