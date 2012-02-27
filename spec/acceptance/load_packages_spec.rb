require 'spec_helper'
require 'homedir'

describe "Loading packages" do
  let (:package_names) do
    EXAMPLES_DIR.children.map { |p| p.basename.to_s }
  end
  context "with the example packages" do
    let(:catalog) { Homedir::Catalog.new }
    let(:pdl) { Homedir::PackageDiscoveryLoader.new(catalog) }

    it "should load all packages" do
      pdl.load_from_directory(EXAMPLES_DIR)
      catalog.map { |p| p.name }.should == package_names
    end
  end
end
