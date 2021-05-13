/* Array first and last */
Object.assign(Array.prototype, {
  first: function() {
    var O = Object(this);
    return O.length ? O[0] : undefined;
  },
  last: function() {
    var O = Object(this);
    return O.length ? O[O.length - 1] : undefined;
  }
});

/* AJAX helpers */
(function() {
  function getAddlAjaxOptions(method, data) {
    switch (method) {
    case "PUT": case "POST":
      if (data instanceof FormData) {
        return {
          contentType: false,
          processData: false
        }
      }
      return {
        data: JSON.stringify(data),
        contentType: "application/json",
        dataType: "json"
      }
    }
  }

  function ajaxHelper(method, url, data) {
    return $.ajax(Object.assign({
      url: url,
      type: method,
      data: data,
      cache: false,
      beforeSend: function(xhr) {
        xhr.setRequestHeader("Accept", "application/json")
        xhr.setRequestHeader("X-CSRFToken", Cookies.get("csrftoken"))
      }
    }, getAddlAjaxOptions(method, data)))
  }

  window.ajaxGet = function(url, data) {
    return ajaxHelper("GET", url, data)
  }

  window.ajaxPost = function(url, data) {
    return ajaxHelper("POST", url, data)
  }

  window.ajaxPut = function(url, data) {
    return ajaxHelper("PUT", url, data)
  }

  window.ajaxDelete = function(url, data) {
    return ajaxHelper("DELETE", url, data)
  }
})();

/* Hamburger menu */
$(".hamburger").click(function() {
  var burger = $(this);
  (burger[burger.hasClass("rotated") ? "removeClass" : "addClass"])("rotated");
  $(".hamburger-menu").slideToggle("slow");
})

/* Content catalog */
function loadContentIndex() {
  var contentIndex = {
    allSections: [], /* List of sections */
    allVariants: [], /* List of variants */
    byId: {},        /* Dictionary of section ID to section info. */
    variantById: {}, /* Dictionary of variant ID to variant info. */
    byName: {},      /* Dictionary of section name to section info. */
    bySlot: {},      /* Dictionary of slot name to ordered list of sections. */
    addSection: function(section) {
      this.allSections.push(section);
      this.byId[section.id] = section;
      this.byName[section.name] = section;
      if (!this.bySlot[section.slot]) {
        this.bySlot[section.slot] = []
      }
      this.bySlot[section.slot].push(section);
    },
    addVariant: function(variant) {
      this.allVariants.push(variant);
      var section = this.byId[variant.section];
      section.variants.push(variant);
      this.variantById[variant.id] = variant;
    }
  }

  function loadSections() {
    return ajaxGet("/api/1.0/cs").catch(function(err) {
      alert("Error loading content catalog.");
    });
  }

  function insertAllSections(allSections) {
    for (var i = 0; i < allSections.length; ++i) {
      var section = Object.assign({}, allSections[i], { variants: [] });
      contentIndex.addSection(section);
    }
  }

  function loadVariants() {
    return ajaxGet("/api/1.0/cv").catch(function(err) {
      alert("Error loading content catalog.");
    });
  }

  function insertAllVariants(allVariants) {
    for (var i = 0; i < allVariants.length; ++i) {
      var variant = Object.assign({}, allVariants[i]);
      contentIndex.addVariant(variant);
    }
  }

  return loadSections().then(function(allSections) {
    insertAllSections(allSections);
    return loadVariants().then(function(allVariants) {
      insertAllVariants(allVariants);
      return contentIndex;
    })
  })
}

/* Page configuration */
function loadPageConfiguration(pageKey, contentIndex) {
  var sections = [];
  var byId = {};
  var empty = false;

  function init(data) {
    if (data.config) {
      sections = data.config.sections || [];
      for (var i = 0; i < sections.length; ++i) {
        var s = sections[i];
        byId[s.sid] = s;
      }
    }
  }

  function cons() {
    return {
      isEmpty: isEmpty,
      useTemplate: useTemplate,
      isResolved: isResolved,
      addSection: addSection,
      removeSection: removeSection,
      resolveAll: resolveSlot,
      resolveSlot: resolveSlot,
      hasGroup: hasGroup,
      addGroup: addGroup,
      removeGroup: removeGroup,
      loadSlotText: loadSlotText,
      contains: contains,
      save: save
    }
  }

  function isEmpty() {
    return empty;
  }

  function contains(sectionId) {
    return !!byId[sectionId];
  }

  function isResolved() {
    for (var i = 0; i < sections.length; ++i) {
      var sectionConfig = sections[i];
      if (!sectionConfig.vid && chooseVariant(sectionConfig.sid)) {
        return false;
      }
    }
    return true;
  }

  function resolveSlot(slotName) {
    for (var i = 0; i < sections.length; ++i) {
      var sectionConfig = sections[i];
      var sectionId = sectionConfig.sid;
      if (!slotName || contentIndex.byId[sectionId].slot == slotName) {
        sectionConfig.vid = chooseVariant(sectionId);
      }
    }
  }

  function chooseVariant(sectionId) {
    var variants = contentIndex.byId[sectionId].variants;
    if (variants && variants.length) {
      var variant = variants[Math.floor(Math.random() * variants.length)];
      return variant.id
    }
    return null;
  }

  function forEachContentSection(doSomething) {
    for (var i = 0; i < contentIndex.allSections.length; ++i) {
      var section = contentIndex.allSections[i];
      doSomething(section);
    }
  }

  function useTemplate(keepAllSections) {
    sections.splice(0, sections.length);
    for (var key in byId) {
      delete byId[key];
    }
    empty = false;
    forEachContentSection(function(section) {
      if (!section.group || keepAllSections) {
        addSection(section);
      }
    })
  }

  function addSection(contentIndexSection) {
    var sectionId = contentIndexSection.id;
    var sectionName = contentIndexSection.name;
    if (!byId[sectionId]) {
      var section = { sid: sectionId, name: sectionName };
      sections.push(section);
      byId[sectionId] = section;
    }
  }

  function removeSection(sectionId) {
    delete byId[sectionId];
    var index = sections.findIndex(function(ele) {
      return ele.sid === sectionId;
    })
    if (index >= 0) {
      sections.splice(index, 1);
    }
  }

  function hasGroup(groupName) {
    var has = false;
    forEachContentSection(function(section) {
      if (section.group === groupName && !!byId[section.id]) {
        has = true;
      }
    })
    return has;
  }

  function addGroup(groupName) {
    forEachContentSection(function(section) {
      if (section.group === groupName) {
        addSection(section);
      }
    });
  }

  function removeGroup(groupName) {
    forEachContentSection(function(section) {
      if (section.group === groupName) {
        removeSection(section.id);
      }
    });
  }

  function loadSlotText(slotName) {
    var data = {
      config: {
        sections: sections
      }
    };
    if (slotName) {
      data.slot = slotName;
    }
    return ajaxPost("/api/1.0/content", {
      key: pageKey,
      config: {
        sections: sections
      }
    })
    .catch(function(err) {
      alert("Error loading page text.");
    });
  }

  function save() {
    return ajaxPost("/api/1.0/ccfg", {
      key: pageKey,
      config: {
        sections: sections
      }
    })
    .catch(function(err) {
      alert("Error saving page configuration.");
    });
  }

  return new Promise(function(resolve, reject) {
    ajaxGet("/api/1.0/ccfg/" + pageKey)
    .then(function(data) {
      init(data);
      resolve(cons());
    })
    .catch(function(err) {
      if (err.status == 404) {
        empty = true;
        resolve(cons());
      }
      else {
        reject(err);
      }
    })
  })
}
