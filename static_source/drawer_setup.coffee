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


$(document).ready ->
    brozar = new FierceBrozar
        mode    : 'continuous'
        query   : params.brozar.query
        url     : "//#{ params.CONTENT_API_ROOT }?token=#{ params.READER_TOKEN }"
        parseResponse: (response) ->
            return _.map response, (item) ->
                return {
                    cover_url: Brozar.extractCover(item)?['1280']
                    published_date: item.first_published_date
                    category: item.category or ''
                    title: item.title
                    link: "/#{ item.slug }/"
                }
            
        itemTemplate: _.template """
            <a class="Brozar_item" href="{{ link }}">
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
            brozar: brozar

    brozar.$el.find('.Drawer_close').on 'click', ->
        top_drawer.close()