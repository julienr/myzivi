// initialWorkspecs is a list of JSON workspecs
// N is the namespace to use for this app
function initMap(initialWorkspecs, N) {
    N.WorkSpec = Backbone.Model.extend({});

    N.WorkSpecList = Backbone.Collection.extend({
        model: N.WorkSpec,
    });

    N.workspecs = new N.WorkSpecList;

    N.WorkSpecView = Backbone.View.extend({
        tagName: "li",
        template: _.template($('#workspec_template').html()),
        initialize: function() {
            this.render();
        },
        render: function() {
            this.$el.html(this.template(this.model.toJSON()));
            return this;
        },
    });

    N.AppView = Backbone.View.extend({
        el: $("#mapapp"),
        initialize: function() {
            N.workspecs.bind('add', this.addOne, this);
            N.workspecs.bind('reset', this.addAll, this);
            N.workspecs.bind('all', this.render, this);
            //workspecs.fecth();
        },

        addOne: function(workspec) {
            var view = new N.WorkSpecView({model: workspec});
            this.$("#workspec-list").append(view.render().el);
        },

        addAll: function() {
            N.workspecs.each(this.addOne);
        },
    });

    N.App = new N.AppView;

    // Populate with initial data
    _.each(initialWorkspecs, function(jsonws){
        var ws = new N.WorkSpec({
            shortname: jsonws.fields.shortname,
            url: jsonws.fields.url,
        });
        N.workspecs.add(ws);
    });

}
