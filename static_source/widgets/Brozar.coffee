console.log 'Brozar.coffee'

is_mobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry/i.test(navigator.userAgent)



class Brozar
    template: -> """
        <div class="Brozar">
            <div class="Brozar_content">
                <div class="Brozar_scroller"></div>
            </div>
            <button class="Brozar_control-next">Next</button>
            <button class="Brozar_control-previous">Previous</button>
        </div>
    """
    constructor: (options) ->
        @_contents = []
        @_options = _.extend
            mode: 'continuous'
            query: {}
            parseResponse: (r) -> r
        , options
        
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
            @ui.previous.hide()
            @ui.next.hide()
        else
            unless @_at_max_right
                @ui.next.show()
            else
                @ui.next.hide()
            unless @_at_max_left
                @ui.previous.show()
            else
                @ui.previous.hide()

    onShow: =>
        @_getItemWidth()
        @_updateScrollerWidth()
        @_showOrHideButtons()

    _bindEvents: ->
        @ui.next.on('click', @next)
        @ui.previous.on('click', @previous)
        $(window).on('resize', _.debounce(@onShow, 50))

    _updateScrollerWidth: ->
        @ui.scroller.css
            width: @_contents.length * @_item_width

    _getItemWidth: ->
        @_item_width = @$el.find('.Brozar_item').first().width()

    render: ->
        @ui.scroller.empty()
        _.each @_contents, (item) =>
            $item_el = $(@_options.itemTemplate(item))
            $item_el.on 'click', (e) ->
                e.preventDefault()
                _.defer ->
                    window.location = $item_el.attr('href')
            @ui.scroller.append($item_el)

    load: ->
        $.ajax
            url: @_options.url
            data: @_options.query
            success: (response) =>
                @_contents = @_options.parseResponse(response)
                @render()

    next: =>
        @_scroll((@ui.content.width() - @_item_width) * -1)

    previous: =>
        @_scroll(@ui.content.width() - @_item_width)

    _scroll: (distance) =>
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


