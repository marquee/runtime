$body = $('body')


class FierceBrozar extends Brozar
    template: -> """
        <div class="Brozar">
            <div class="Brozar_content">
                <div class="Brozar_scroller"></div>
            </div>
            <div class="Brozar_controls">
                <button class="Drawer_close">Close</button>
                <button class="Brozar_control-next">Next</button>
                <button class="Brozar_control-previous">Previous</button>
            </div>
        </div>
    """

MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

formatDate = (d) ->
    return "#{ MONTHS[d.getMonth()] } #{ d.getDate() }, #{ d.getFullYear() }"



class ShareView
    constructor: ->
        url = escape(window.location.href)
        text = escape($('title').text())
        @$el = $("""<div class="ShareView">
                <a class="share_link" href="https://plus.google.com/share?url=#{ url }">Google+</a>
                <a class="share_link" href="https://www.facebook.com/sharer.php?u=#{ url }&t=#{ text }">Facebook</a>
                <a class="share_link" href="http://twitter.com/intent/tweet?source=#{ params.twitter_screen_name }&url=#{ url }&text=#{ text }">Twitter</a>
            </div>""")
        @el = @$el[0]



$(document).ready ->
    brozar = new FierceBrozar
        mode    : 'continuous'
        query   : params.brozar.query
        url     : "//#{ params.CONTENT_API_ROOT }?token=#{ params.READER_TOKEN }"
        parseResponse: (response) ->
            return _.map response, (item) ->
                return {
                    cover_url       : Brozar.extractCover(item)?['1280']
                    published_date  : formatDate(new Date(item.first_published_date))
                    category        : item.category or ''
                    title           : item.title
                    link            : "/#{ item.slug }/"
                }
            
        itemTemplate: _.template """
            <a class="Brozar_item item-fifth" href="{{ link }}">
                <div class="item_cover" style="background-image: url({{ cover_url }})"></div>
                <div class="item_info">
                    <div class="item_supertitle">
                        <span class="published_date">{{ published_date }}</span>
                        <span class="category">{{ category }}</span>
                    </div>
                    <div class="item_title">{{ title }}</div>
                </div>
            </a>
        """

    brozar.load()

    top_drawer = new Drawer
        els_to_move: ['#site-header', '#view-content']
        content:
            brozar  : brozar
            share   : new ShareView()

    brozar.$el.find('.Drawer_close').on 'click', ->
        top_drawer.close()
