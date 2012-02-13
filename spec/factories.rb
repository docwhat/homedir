require 'homedir'

FactoryGirl.define do
  factory :package, :class => Homedir::Package do
    sequence(:name) { |n| "package-name-#{n}"}
    sequence(:description) { |n| "package description #{n}" }
    directory { File.join("test-directory", "#{name}") }
  end
end
