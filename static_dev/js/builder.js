(function() {
  var navState = window.navState;

  $("#website-select").on("change", function() {
    var domain = $(this).find("option:selected").val();
    if (domain) {
      navState.website = domain;
      checkNav();
    }
  })
  $("#year-select").on("change", function() {
    var year = $(this).find("option:selected").val();
    if (year) {
      navState.year = year;
      checkNav();
    }
  })
  $("#make-select").on("change", function() {
    var make = $(this).find("option:selected").val();
    if (make && make != navState.make) {
      navState.make = make;
      navState.model = "";
      $(".model-select").hide();
      $("#" + make + "-model-select").show();
    }
  })
  $(".model-select").on("change", function() {
    var model = $(this).find("option:selected").val();
    if (model) {
      navState.model = model;
      checkNav();
    }
  })

  function checkNav() {
    var newPath = null;
    if (navState.website) {
      if (!newPath) {
        newPath = "/content/builder";
      }
      newPath += "/";
      newPath += navState.website;
    }
    if (navState.year && navState.make && navState.model) {
      if (!newPath) {
        newPath = "/content/builder/000";
      }
      newPath += "/";
      newPath += getSlug();
    }
    if (newPath && newPath != window.location.pathname) {
      window.location.href = newPath;
    }
  }

  function forSlug(value) {
    return value.replace(/[\s-]/g, "").toLowerCase();
  }

  function getContentKey() {
    return navState.website + "-" + getSlug();
  }

  function getSlug() {
    var slug = navState.make + "-" + navState.model;
    if (navState.year !== "*") {
      slug = navState.year + "-" + slug;
    }
    return slug;
  }

  var contentIndex;
  var pageConfiguration;
  var currentImages;

  var showRendered;
  var dirty;

  function reset() {
    return loadContentIndex().then(function(data) {
      contentIndex = data;
      return loadPageConfiguration(getContentKey(), contentIndex).then(function(obj) {
        pageConfiguration = obj;
        return loadImages().then(function(data) {
          currentImages = data;
          prepImages();
        })
      })
    })
  }

  if (navState.make && navState.model) {
    reset().then(renderPageConfiguration)
  }

  function loadImages() {
    return ajaxGet("/api/1.0/media", {
      year: navState.year,
      make: navState.make,
      model: navState.model
    })
    .catch(function(err) {
      toastr.error(err);
    })
  }

  function prepImages() {
    if (!currentImages || !currentImages.length) {
      $("#no-images-warning").show();
      pageConfiguration.removeGroup("image");
    }
    else {
      renderImages();
    }
  }

  function renderImages() {
    $(".image-bar").empty();
    var anySelected = false;
    for (var i = 0; i < currentImages.length; ++i) {
      renderImage(currentImages[i]);
    }
    if (currentImages.length < 3) {
      $(".add-images").show();
    }
    else {
      $(".add-images").hide();
    }
    if (!$(".image-frame.selected").length) {
      $($(".image-frame")[0]).click();
    }
    $(".image-bar").show();
    $("#no-images-warning").hide();
  }

  function renderImage(image) {
    var imageFrame = 
      $("<div>").addClass("image-frame").append(
        $("<img>").attr("src", image.url));
    if (pageConfiguration.isSelectedImage(image)) {
      imageFrame.addClass("selected");
    }
    imageFrame.on("click", function(e) {
      if (!pageConfiguration.isSelectedImage(image)) {
        pageConfiguration.selectImage(image);
        dirty = true;
        reloadSlotText()
        updatePageControls();
        $(".image-frame.selected").removeClass("selected");
        $(this).addClass("selected");
      }
    })
    $(".image-bar").append(imageFrame);
  }

  $("#starter-button").click(function(e) {
    var deluxe = !!$("#starter-deluxe-checkbox").prop("checked");
    pageConfiguration.useTemplate(deluxe);
    dirty = true;
    renderPageConfiguration();
  });

  function renderPageConfiguration() {
    if (pageConfiguration.isEmpty()) {
      $("#empty-case-div").show() 
      $("#toc").hide();
    }
    else {
      $("#empty-case-div").hide();
      $(".slot-div").each(function() {
        var slotName = $(this).attr("data-name");
        $(this).find(".sections-div").each(function() {
          $(this).empty();
          var sectionsForSlot = contentIndex.bySlot[slotName];
          if (sectionsForSlot) {
            for (var i = 0; i < sectionsForSlot.length; ++i) {
              var section = sectionsForSlot[i];
              $(this).append(renderSectionControl(section))
            }
          }
        })
      });
      reloadSlotText();
      updatePageControls();
      $("#toc").show();
    }
  }

  function reloadSlotText(slotName) {
    pageConfiguration.loadSlotText(slotName).then(function(data) {
      $.each(data, function(slotName, slotContent) {
        $(".slot-div[data-name=" + slotName + "]").find("textarea").text(slotContent)
      });
    })
  }

  function renderSectionControl(section) {
    var isDeadImage = section.group === "image" && (!currentImages || !currentImages.length);

    var checkbox = $("<input type='checkbox'>")
      .attr("checked", pageConfiguration.contains(section.id));

    if (isDeadImage) {
      checkbox.attr("disabled", true);
    }
    else {
      checkbox.on("click", function() {
        if (pageConfiguration.contains(section.id)) {
          pageConfiguration.removeSection(section.id);
        }
        else {
          pageConfiguration.addSection(section);
          pageConfiguration.resolveSlot(section.slot);
        }
        dirty = true;
        updatePageControls();
        reloadSlotText(section.slot);
      });
    }

    var label = $("<span>")
      .attr("class", "section-name")
      .text(section.name + " ");

    if (section.group === "deluxe") {
      label.append($("<span>").text(" \u2606"));
    }
    if (isDeadImage) {
      label.append(
          $("<span class='tooltip-container'>")
              .append($("<span>").html(" &#x24d8; "))
              .append($("<span class='tooltip-text'>")
                  .text("This section cannot be shown unless images are added for this make/model.")));
    }

    var div = $("<div>").attr("class", "section-div");
    div.append(checkbox);
    div.append(label);
    return div;
  }

  function updatePageControls() {
    $("#deluxe-group-checkbox").prop("checked", pageConfiguration.hasGroup("deluxe"));
    $("#save-button").prop("disabled", !dirty);
    $("#preview-button").prop("disabled", dirty || !pageConfiguration.isResolved());
    $("#preview-unformatted-button").prop("disabled", !pageConfiguration.isResolved());
  }

  $(".copy-button").on("click", function() {
    const textarea = $(this).closest(".textarea-container").find("textarea")[0];
    textarea.select()
    textarea.setSelectionRange(0, 9999);
    document.execCommand("copy");
    alert("Copied");
  })

  $("#deluxe-group-checkbox").on("click", function() {
    if (pageConfiguration.hasGroup("deluxe")) {
      pageConfiguration.removeGroup("deluxe");
    }
    else {
      pageConfiguration.addGroup("deluxe");
    }
    dirty = true;
    renderPageConfiguration();
  })

  $("#reset-button").on("click", function() {
    var deluxe = pageConfiguration.hasGroup("deluxe");
    reset().then(function() {
      pageConfiguration.useTemplate(deluxe);
      dirty = true;
      renderPageConfiguration();
      toastr.success("Content reset.")
    });
  });

  $("#save-button").on("click", function() {
    pageConfiguration.save().then(function() {
      dirty = false;
      updatePageControls()
      toastr.success("Page configuration saved.")
    });
  });

  $(".randomize-slot-button").on("click", function() {
    var slotName = $(this).closest(".slot-div").attr("data-name");
    pageConfiguration.resolveSlot(slotName);
    dirty = true;
    reloadSlotText(slotName)
    updatePageControls()
  });

  $("#randomize-button").on("click", function() {
    pageConfiguration.resolveAll();
    dirty = true;
    reloadSlotText()
    updatePageControls()
    toastr.success("Content randomized.")
  });

  $("#preview-button").on("click", function() {
    var url = "/content/preview?website=" + navState.website + "&slug=" + getSlug();
    window.open(url, "_blank");
  });

  $("#preview-unformatted-button").on("click", function() {
    pageConfiguration.loadSlotText().then(function(data) {
      var template = $('<div class="preview"><div class="slot-header"></div><div class="slot-body"></div><div class="slot-footer"></div></div>')
      var modal = $(".ModalWindow .preview-container").empty().append(template);
      $.each(data, function(slotName, slotContent) {
        modal.find(".slot-" + slotName).append(slotContent);
      });
      openModal();
    })
  });

  document.addEventListener("keydown", function(e) {
    if (e.keyCode == 27/*esc*/) {
      closeModal();
    }
  });

  $(".ModalScreen").on("click", function(e) { closeModal() });
  $(".ModalWindow").on("click", function(e) { e.stopPropagation() });
  $(".ModalWindow .titlebar").on("click", function(e) { e.stopPropagation() });
  $(".ModalWindow .body").on("click", function(e) { e.stopPropagation() });
  $(".ModalWindow .x").on("click", function(e) { closeModal() });

  function openModal() {
    $(".ModalScreen").show();
  }

  function closeModal() {
    $(".ModalScreen").hide();
  }
})();
