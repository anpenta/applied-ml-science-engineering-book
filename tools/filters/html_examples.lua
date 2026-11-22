-- Render worked examples as styled containers in the HTML edition.
function BlockQuote(block)
  local first = block.content[1]
  if not first or first.t ~= "Para" then return nil end
  local lead = first.content[1]
  if not lead or lead.t ~= "Strong" then return nil end
  if not pandoc.utils.stringify(lead):match("^Worked example:") then return nil end
  return pandoc.Div(block.content, pandoc.Attr("", {"worked-example"}))
end
