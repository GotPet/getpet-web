"use strict";
app.config({
    autoload: !0,
    provide: [],
    googleApiKey: "",
    googleAnalyticsId: "",
    smoothScroll: !1,
    saveState: !1,
    cacheBust: "v=40"
}), app.ready(function () {
    if (window.Bloodhound) {
        let a = new Bloodhound({
            datumTokenizer: Bloodhound.tokenizers.obj.whitespace("tokens"),
            queryTokenizer: Bloodhound.tokenizers.whitespace,
            prefetch: {
                url: app.dir.assets + "data/json/files.json",
                cache: !1
            }
        });
        $("#theadmin-search input").typeahead(null, {
            name: "theadmin-components",
            display: "title",
            source: a,
            templates: {
                suggestion: function (a) {
                    return '<a href="' + location.origin + "/theadmin/" + a.url + '"><h6 class="mb-1">' + a.title + "</h6><small>" + a.description + "</small></a>"
                }
            }
        }), $("#theadmin-search input").bind("typeahead:select", function (a, b) {
            window.location.href = location.origin + "/theadmin/" + b.url
        }), $("#theadmin-search input").bind("typeahead:open", function (a, b) {
            $(this).closest("#theadmin-search").find(".lookup-placeholder span").css("opacity", "0")
        }), $("#theadmin-search input").bind("typeahead:close", function (a, b) {
            "" === $(this).val() && $(this).closest("#theadmin-search").find(".lookup-placeholder span").css("opacity", "1")
        })
    }
});