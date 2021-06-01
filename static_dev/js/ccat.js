var contentIndex;
var selection;
var currentSection;
var currentVariantIndex = 0;

loadContentIndex().then(function(data) {
  contentIndex = data;
  renderSections();
})

function renderSections() {
  for (var i = 0; i < slots.length; ++i) {
    var slot = slots[i];
    var sections = contentIndex.bySlot[slot];
    if (sections) {
      for (var j = 0; j < sections.length; ++j) {
        renderSection(sections[j], slot);
      }
    }
  }
}

function renderSection(section, slot) {
  var row = $("<li>").attr("data-name", section.name);
  row.append($('<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 20 20"><title>draggable</title><path d="M2 11h16v2H2zm0-4h16v2H2zm8 11l3-3H7l3 3zm0-16L7 5h6l-3-3z"/></svg>'))
  row.append($("<div>").text(section.name));
  row.append($("<div>").text(""));
  $(".slot-info-div[data-name='" + slot + "'] ul.reorder-list").append(row);
  row.on("click", function(e) {
    selectSection(section);
  });
}

function selectSection(section) {
  $(".slot-info-div li").removeClass("selected");
  $(".slot-info-div li[data-name='" + section.name + "']").addClass("selected");
  currentSection = section;
  $(".selected-section-div").show();
  $("#selected-section-span").text(currentSection.name);
  $("input[name='deluxe'").prop("checked", currentSection.group === "deluxe");
  $("input[name='image'").prop("checked", currentSection.group === "image");
  currentVariantIndex = 0;
  renderCurrentVariant();
}

$(".reorder-list").sortable({
  start: function(event, ui) {
    var startingPos = ui.item.index();
    ui.item.data("startingPos", startingPos);
  },
  update: function(event, ui) {
    var startingPos = ui.item.data("startingPos")
    var endingPos = ui.item.index()
    var slot = ui.item.closest(".slot-info-div").attr("data-name")
    var sections = contentIndex.bySlot[slot];
    var mover = sections[startingPos];
    sections.splice(startingPos, 1)
    sections.splice(endingPos, 0, mover)
    transmitNewOrder(slot, sections)
  }
});
$("#reorder-list").disableSelection();

function transmitNewOrder(slot, sections) {
  var order = null;
  for (var i = 0; i < sections.length; ++i) {
    var section = sections[i];
    if (order === null) {
      order = section.order || 0;
    }
    else {
      order += 1;
    }
    if (order !== section.order) {
      section.order = order;
      var data = Object.assign({}, section);
      delete data.variants;
      ajaxPut("/api/1.0/cs/" + data.id, data)
    }
  }
}

$(".add-section-button").on("click", function() {
  var sectionName = $(this).parent().find(".section-name-input").val();
  if (!sectionName) {
    toastr.warning("Enter new section name.")
    return;
  }
  if (contentIndex.byName[sectionName]) {
    toastr.warning("That section already exists.")
    return;
  }
  var slot = $(this).closest(".slot-info-div").attr("data-name");
  var lastSection = contentIndex.bySlot[slot] && contentIndex.bySlot[slot].last()
  var bottom = lastSection ? lastSection.order + 1 : 0;
  ajaxPost("/api/1.0/cs", { name: sectionName, slot: slot, order: bottom })
  .then(function(data) {
    data.variants = [];
    contentIndex.addSection(data);
    renderSection(data, slot);
    selectSection(data);
  })
  .catch(function(err) {
    toastr.error("Error adding section.");
  });
})

function renderCurrentVariant() {
  if (currentSection && currentSection.variants && currentSection.variants.length > 0) {
    $("#the-textarea").show()
    $("#the-textarea").attr("readonly", true);
    $("#the-textarea").val("(Loading...)");
    loadCurrentText(currentSection.variants[currentVariantIndex]).then(function(text) {
      $("#the-textarea").val(text);
      $("#the-textarea").attr("readonly", false);
      $("#save-button-div").show()
    });
  }
  else {
    $("#the-textarea").hide()
  }
  refreshVariantNav();
}

function refreshVariantNav() {
  $("#variant-nav-div").hide();
  if (!currentSection) return;
  var nvariants = currentSection.variants.length;
  if (nvariants == 0) {
    $("#got-variants-span").hide();
    $("#no-variants-span").show();
  }
  else {
    $("#got-variants-span").show();
    $("#no-variants-span").hide();
    $("#variant-index-span").text(currentVariantIndex + 1)
    $("#nvariants-span").text(nvariants);
  }
  if (nvariants < 2) {
    $("#prev-variant-link").hide();
    $("#next-variant-link").hide();
  }
  else {
    $("#prev-variant-link").show();
    $("#next-variant-link").show();
  }
  $("#variant-nav-div").show();
}

function loadCurrentText(variant) {
  return new Promise(function(resolve, reject) {
    ajaxGet("/api/1.0/cv/" + variant.id)
      .then(function(data) {
        resolve(data.text);
      })
      .catch(function(err) {
        if (err.status == 404) {
          resolve("");
        }
        else {
          toastr.error("Error loading content.");
          reject(err);
        }
      });
  })
}

$("input[name='deluxe']").on("click", function() {
  currentSection.group = this.checked ? "deluxe" : "";
  ajaxPut("/api/1.0/cs/" + currentSection.id, currentSection)
})

$("input[name='image']").on("click", function() {
  var oldGroup = currentSection.group;
  if (this.checked) {
    currentSection.group = "image";
  }
  else if (currentSection.group === "image") {
    currentSection.group = null;
  }
  if (oldGroup === currentSection.group) return;
  ajaxPut("/api/1.0/cs/" + currentSection.id, currentSection)
})

$("#prev-variant-link").on("click", function() {
  if (currentVariantIndex > 0) {
    currentVariantIndex -= 1;
    renderCurrentVariant();
  }
})
$("#next-variant-link").on("click", function() {
  if (currentVariantIndex < currentSection.variants.length - 1) {
    currentVariantIndex += 1;
    renderCurrentVariant();
  }
})

$("#add-variant-button").on("click", function() {
  if (!currentSection) return;
  ajaxPost(
    "/api/1.0/cv",
    { section: currentSection.id, text: "<p>Your HTML here.  Don't forget to click Save.</p>" }
  )
  .then(function(data) {
    contentIndex.addVariant(data);
    currentVariantIndex = currentSection.variants.length - 1;
    renderCurrentVariant();
    $("#the-textarea").val(data.text);
    $("#the-textarea").attr("readonly", false);
  })
  .catch(function(err) {
    toastr.error("Error adding section.");
  })
})

$("#save-button").on("click", function() {
  if (!currentSection || !currentSection.variants.length) return;
  var id = currentSection.variants[currentVariantIndex].id;
  var text = $("#the-textarea").val();
  ajaxPut("/api/1.0/cv/" + id, { section: currentSection.id, text: text })
  .then(function(data) {
    toastr.success("Saved.")
  })
  .catch(function(err) {
    toastr.error("Error saving text.");
  })
})

$("#delete-button").on("click", function() {
  var id;
  try {
    id = currentSection.variants[currentVariantIndex].id;
  }
  catch (e) {
    return;
  }
  ajaxDelete("/api/1.0/cv/" + id)
  .then(function() {
    toastr.success("Deleted.")
    currentSection.variants.splice(currentVariantIndex, 1);
    currentVariantIndex = Math.min(currentVariantIndex, currentSection.variants.length - 1)
    renderCurrentVariant();
  })
  .catch(function(err) {
    toastr.error("Error deleting content variant.");
  })
})
