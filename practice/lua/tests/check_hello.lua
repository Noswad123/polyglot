local source, report = arg[1], arg[2]
local stdout = io.stdout
local function finish(state, message)
    if message then io.stderr:write(tostring(message), "\n") end
    local file = assert(io.open(report, "w"))
    file:write(state, "\n")
    file:close()
    if state ~= "passed" then os.exit(1) end
end
local function position()
    local flushed, flush_error = stdout:flush()
    local offset, seek_error = stdout:seek()
    if not flushed or not offset then
        finish("blocked", "Cannot measure stdout: regular-file flush/seek support is required: " .. tostring(flush_error or seek_error))
    end
    return offset
end
local chunk, err = loadfile(source)
if not chunk then finish("failed", err) end
local ok, message = pcall(chunk)
if not ok then finish("failed", message) end
local load_output = position()
if type(hello) ~= "function" then
    finish("failed", "Expected global function hello")
end
local function inspect(...)
    local count = select("#", ...)
    local succeeded, value = ...
    if not succeeded then finish("failed", value) end
    if count > 2 or value ~= nil then
        finish("failed", "hello must return no values or a single nil")
    end
end
inspect(pcall(hello))
local function_output = position() - load_output
if load_output ~= 0 then
    finish("failed", "Source must not write stdout; put the greeting inside hello")
end
if function_output ~= #"Hello, World!\n" then
    finish("failed", "hello must write exactly Hello, World! followed by one newline")
end
finish("passed")
