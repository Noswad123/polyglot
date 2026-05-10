-- Set variables
local number = 5

local truth, lies = true, false
local nothing = nil

local greet = function(name)
	print("hello!", name)
end

local liar_greet = function(is_lying)
  if is_lying then
    greet("frank")
  else
    greet("jamal")
  end
end

liar_greet(truth)

liar_greet(lies)

-- these are the same
-- function MyTable.something(Self, ...) end
-- function MyTable:something(...) end

local tbl = {1, 2, 3, 35, 3}
for index, value in pairs(tbl) do
  print(index, value)
end

local nums = {1, 2, 3, 35, 3}
print(table.concat(nums, "3"))
print(#nums) -- gives you the length of nums
for i =1, #nums do
  print(nums[i])
end


io.output("myfile.txt")
io.close()
