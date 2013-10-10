

is_mobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry/i.test(navigator.userAgent)



class Brozar
    template: -> """
        <div class="Brozar">
            <div class="Brozar_content">
                <div class="Brozar_scroller"></div>
            </div>
            <div class="Brozar_controls">
                <button class="Brozar_control-next">Next</button>
                <button class="Brozar_control-previous">Previous</button>
            </div>
        </div>
    """
    constructor: (options) ->
        @_contents = []
        @_options = _.extend
            mode        : 'continuous'
            query       : {}
            api_root    : 'http://marquee.by/content/'
            limit       : 10
            parseResponse: (r) -> r
        , options
        @_loaded_all = false
        @_page_loaded = -1
        @_num_loaded = 0
        
        @$el = $(@template())
        @el = @$el[0]

        @ui =
            content     : @$el.find('.Brozar_content')
            next        : @$el.find('.Brozar_control-next')
            previous    : @$el.find('.Brozar_control-previous')
            scroller    : @$el.find('.Brozar_scroller')
        
        if is_mobile
            @ui.next.remove()
            @ui.previous.remove()
        else
            @_setUpScroll()
        @_bindEvents()
        @_getItemWidth()
        @_showOrHideButtons()

    _setUpScroll: ->
        @_current_left = 0
        @_at_max_left = true
        @_at_max_right = false

        @ui.scroller.css
            left: @_current_x

    _showOrHideButtons: ->
        if @ui.content.width() >= @ui.scroller.width()
            @ui.previous.attr('disabled', true)
            @ui.next.attr('disabled', true)
        else
            unless @_at_max_right
                @ui.next.removeAttr('disabled')
            else
                @ui.next.attr('disabled', true)
            unless @_at_max_left
                @ui.previous.removeAttr('disabled')
            else
                @ui.previous.attr('disabled', true)

    onShow: =>
        @_getItemWidth()
        @_updateScrollerWidth()
        @_showOrHideButtons()
        @_scroll(0)

    _bindEvents: ->
        @ui.next.on('click', @next)
        @ui.previous.on('click', @previous)
        @ui.content.on 'scroll', _.debounce =>
            @_scroll(0, load_anyway=true)
        , 50
        $(window).on('resize', _.debounce(@onShow, 50))

    _updateScrollerWidth: =>
        @ui.scroller.css
            width: @_num_loaded * @_item_width

    _getItemWidth: =>
        @_item_width = @$el.find('.Brozar_item').first().width()

    render: ->
        _.each @_contents, (item) =>
            $item_el = $(@_options.itemTemplate(item))
            $item_el.on 'click', (e) ->
                e.preventDefault()
                _.defer ->
                    window.location = $item_el.attr('href')
            @ui.scroller.append($item_el)

    load: (page=0) ->
        unless @_loaded_all or @_is_loading
            @_is_loading = true
            offset = page * @_options.limit
            @_contents = []
            @_page_loaded = page
            $.ajax
                url: @_options.api_root
                data: @_options.query
                headers:
                    'Authorization'             : "Token #{ @_options.token }"
                    'X-Content-Query-Limit'     : @_options.limit
                    'X-Content-Query-Offset'    : offset
                success: (response) =>
                    @_is_loading = false
                    @_contents = @_options.parseResponse(response)
                    if @_contents.length is 0
                        @_loaded_all = true
                    else
                        @_num_loaded += @_contents.length
                        @render()
                        _.defer(@onShow)

    next: =>
        @_scroll((@ui.content.width() - @_item_width) * -1)

    previous: =>
        @_scroll(@ui.content.width() - @_item_width)

    _scroll: (distance, load_anyway=false) =>
        min_left = -1 * @ui.scroller.width() + @ui.content.width()
        max_left = 0
        new_left = @_current_left + distance

        @_at_max_right = false
        @_at_max_left = false
        if new_left >= max_left
            new_left = max_left
            @_at_max_left = true
        else if new_left <= min_left
            new_left = min_left
            @_at_max_right = true

        @_current_left = new_left
        @ui.scroller.css
            left: @_current_left

        if (distance < 0 or load_anyway) and min_left < 0 and Math.abs(min_left) - Math.abs(new_left) < 2 * @_item_width
            @load(@_page_loaded + 1)

        @_showOrHideButtons()

    @extractCover = (item) ->
        cover_urls = null
        if item.cover_content?
            if _.isArray(item.cover_content) and item.cover_content.length > 0
                cover_content = item.cover_content[0]
            else if item.cover_content.image?
                cover_content = item.cover_content.image
            else if item.cover_content.content
                cover_content = item.cover_content
            if cover_content?
                cover_urls =
                    '1280': cover_content.content['1280']?.url
                    '640': cover_content.content['640']?.url
        return cover_urls

window.Brozar = Brozar


