-- Set variables
local number = 5

local truth, lies = true, false
local nothing = nil

local greet = function(name)
	print("hello!", name)
end

if lies then
	greet("dawson")
end

greet("jamal")

-- these are the same
function MyTable.something(Self, ...) end
-- function MyTable:something(...) end
