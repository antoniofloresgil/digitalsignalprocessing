-- HTML edition only: make every executed Python cell runnable in the browser.
--
-- Each executed cell keeps its build-time output (and its figure label), but its
-- code becomes an editable Pyodide editor with a Run button (quarto-live). A
-- cell usually needs variables defined by earlier cells, so tools/live_deps.py
-- works out which earlier cells it depends on, reading the source .qmd (which
-- also holds the cells whose code is not shown). Their code is attached as a
-- hidden `setup` block that quarto-live runs, in a fresh environment, before
-- the visible code on every Run. The result: each cell runs correctly on its
-- own, in any order, and always gives the same answer.
--
-- Runs at `pre-ast` (see _quarto.yml) so that quarto-live, which turns the
-- generated `pyodide` blocks into editors, sees them.

local function is_cell_code(block)
  return block.t == "CodeBlock"
    and block.classes:includes("cell-code")
    and block.classes:includes("python")
end

local function has_output(div)
  local found = false
  div:walk({
    Div = function(d)
      if d.classes:includes("cell-output") then found = true end
    end,
  })
  return found
end

-- Cells of the source document: { {code = ..., deps = {0-based indices}}, ... }
local function source_cells()
  local input = quarto.doc.input_file
  local root = quarto.project.directory or "."
  local script = root .. "/tools/live_deps.py"
  local ok, out = pcall(pandoc.pipe, "python3", { script, "--json", input }, "")
  if not ok then
    error("live-cells.lua: could not run " .. script .. " on " .. tostring(input) .. ": " .. tostring(out))
  end
  return quarto.json.decode(out)
end

function Pandoc(doc)
  local cells = nil

  return doc:walk({
    Div = function(div)
      if not div.classes:includes("cell") then return nil end
      local n = tonumber(div.attributes["execution_count"])
      if not n then return nil end
      local with_output = has_output(div)

      return div:walk({
        CodeBlock = function(block)
          if not is_cell_code(block) then return nil end
          cells = cells or source_cells()
          local cell = cells[n]
          if not cell then
            error("live-cells.lua: no source cell number " .. n .. " (document has " .. #cells .. ")")
          end
          local key = "cell-" .. n

          local blocks = {}
          if #cell.deps > 0 then
            local setup = {}
            for _, j in ipairs(cell.deps) do
              table.insert(setup, cells[j + 1].code)
            end
            local payload = { code = table.concat(setup, "\n\n"), attr = { exercise = key, setup = true } }
            table.insert(blocks, pandoc.RawBlock("html",
              '<script type="exercise-setup-' .. key .. '-contents">\n'
              .. quarto.base64.encode(quarto.json.encode(payload))
              .. "\n</script>"))
          end

          local header = table.concat({
            "#| exercise: " .. key,
            "#| caption: Python",
            "#| timelimit: 600",
          }, "\n")
          table.insert(blocks, pandoc.CodeBlock(header .. "\n" .. block.text,
            pandoc.Attr("", { "pyodide" })))
          if with_output then
            table.insert(blocks, pandoc.Div(
              { pandoc.Plain({ pandoc.Str("Output when the book was built") }) },
              pandoc.Attr("", { "live-static-label" })))
          end
          return blocks
        end,
      })
    end,
  })
end
