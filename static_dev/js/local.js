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
      return section.variants.length - 1;
    }
  }
  var contentVariants;

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
