-- Render tables inside worked-example blockquotes as nonbreaking tabularx tables.
-- Pandoc normally emits longtable, which cannot paginate reliably inside
-- the breakable mdframed environment used by the PDF edition.
local function cell_tex(cell)
  local parts = {}
  for _, block in ipairs(cell.contents) do
    local rendered = pandoc.write(pandoc.Pandoc({block}), "latex")
    rendered = rendered:gsub("^%s+", ""):gsub("%s+$", "")
    table.insert(parts, rendered)
  end
  return table.concat(parts, " \\par ")
end

local function convert_table(tbl)
  local rows = {}
  for _, row in ipairs(tbl.head.rows) do table.insert(rows, row) end
  for _, body in ipairs(tbl.bodies) do
    for _, row in ipairs(body.head) do table.insert(rows, row) end
    for _, row in ipairs(body.body) do table.insert(rows, row) end
  end
  for _, row in ipairs(tbl.foot.rows) do table.insert(rows, row) end

  local count = #tbl.colspecs
  if count == 0 or #rows == 0 then return tbl end
  local spec = string.rep(">{\\raggedright\\arraybackslash}X", count)
  local lines = {
    "\\par\\medskip\\noindent",
    "\\begingroup\\footnotesize",
    "\\begin{tabularx}{\\linewidth}{@{}" .. spec .. "@{}}",
    "\\toprule"
  }
  for i, row in ipairs(rows) do
    local cells = {}
    for _, cell in ipairs(row.cells) do
      table.insert(cells, cell_tex(cell))
    end
    table.insert(lines, table.concat(cells, " & ") .. " \\\\")
    if i == #tbl.head.rows and #tbl.head.rows > 0 then
      table.insert(lines, "\\midrule")
    end
  end
  table.insert(lines, "\\bottomrule")
  table.insert(lines, "\\end{tabularx}")
  table.insert(lines, "\\endgroup\\par\\medskip")
  return pandoc.RawBlock("latex", table.concat(lines, "\n"))
end

function BlockQuote(block)
  -- Keep regular quotes unchanged. Only worked examples use the PDF frame.
  local first = block.content[1]
  if not first or first.t ~= "Para" then return nil end
  local lead = first.content[1]
  if not lead or lead.t ~= "Strong" then return nil end
  if not pandoc.utils.stringify(lead):match("^Worked example:") then return nil end
  return pandoc.walk_block(block, {Table = convert_table})
end
