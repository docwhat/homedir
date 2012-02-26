require 'spec_helper'
require 'homedir'

describe "Loading packages" do
  let (:package_names) do
    EXAMPLES_DIR.children.map { |p| p.basename.to_s }
  end
  context "with the example packages" do
    it "should load all packages" do
      pending "not implemented"
      catalog = Homedir::Catalog.new
      catalog.load(EXAMPLES_DIR)
      catalog.map { |p| p.name }.should == package_names
    end
  end
end
