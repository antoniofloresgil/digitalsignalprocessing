-- PDF only: place the contents after the Preface and switch to arabic page
-- numbers where the main matter starts (Part I, or the first numbered
-- chapter in a book without parts). HTML keeps the source order untouched.
local function starts_main_matter(block)
  if block.t == "Div" and block.classes:includes("quarto-book-part") then
    return true
  end
  if block.t == "Header" and block.level == 1
    and not block.classes:includes("unnumbered") then
    return true
  end
  if block.t == "RawBlock" and block.format == "latex" and block.text:match("^\\part") then
    return true
  end
  if block.t == "Para" and block.content[1] and block.content[1].t == "RawInline"
    and block.content[1].text:match("^\\part") then
    return true
  end
  return false
end

function Pandoc(doc)
  if not FORMAT:match("latex") then
    return nil
  end
  for i, block in ipairs(doc.blocks) do
    if starts_main_matter(block) then
      doc.blocks:insert(i, pandoc.RawBlock("latex", "\\BookContents\n\\BookMainMatter"))
      return doc
    end
  end
end
