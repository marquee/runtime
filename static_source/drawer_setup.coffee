$body = $('body')


$(document).ready ->
    brozar = new Brozar
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

