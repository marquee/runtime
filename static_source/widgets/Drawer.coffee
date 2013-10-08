console.log 'Drawer.coffee'

$body = $('body')

prefixProperty = (styles, property, value) ->
    for prefix in ['-webkit-', '-ms-', '-o-', '-moz-', '']
        styles["#{ prefix }#{ property }"] = value

# Public: a nav drawer element. 
#
#     top_drawer = new Drawer
#         els_to_move: ['#site-header', '#view-content']
#         content:
#             brozar: brozar.el
#
class Drawer
    constructor: (_options) ->
        @_options = _.extend
            location            : 'top'
            mode                : 'push' # 'overlay'
            content             : {}
            height              : 260
            transition          : 200
            position            : 'fixed'
            els_to_move         : ['body']
            move_property       : 'margin-top'
            close_on_outside    : true
        , _options
        @$el = $("<div class='Drawer Drawer-#{ @_options.location }'></div>")
        @$el.on 'click', (e) -> e.stopPropagation()
        @el = @$el[0]
        @_captureElements()
        @_setStyles()
        @_bindTriggers()
        @close()
        $body.append(@el)

    _captureElements: ->
        @_moving_els = $(@_options.els_to_move.join(','))

    _bindTriggers: ->
        $('.Drawer_trigger').each (i, el) =>
            $trigger = $(el)
            content_name = $trigger.attr('data-Drawer_content')
            $trigger.on 'click', (e) =>
                e?.stopPropagation()
                is_open = @toggleContent(content_name)
                if is_open
                    $trigger.attr('data-active', true)
                else
                    $trigger.removeAttr('data-active')

    _setStyles: ->
        @_moving_els.each (i, el) =>
            $el = $(el)
            default_value = parseInt($el.css(@_options.move_property))
            default_value ?= 0
            $el.data('default_value', default_value)
            if $el.css('position') is 'static'
                $el.css(position: 'relative')
        body_css = {}
        prefixProperty(body_css, 'transition-property', @_options.move_property)
        prefixProperty(body_css, 'transition-duration', "#{ @_options.transition }ms")
        @_moving_els.css(body_css)

        el_css =
            position: @_options.position
        prefixProperty(el_css, 'transition-property', 'height')
        prefixProperty(el_css, 'transition-duration', "#{ @_options.transition }ms")

        @$el.css(el_css)

    render: ->
        return @el

    open: (e) ->
        e?.stopPropagation()
        @is_open = true
        $body.attr('data-drawer_open', true)
        if @_options.close_on_outside
            $body.off('click', @close).one('click', @close)
        @$el.css
            height: @_options.height
        @_moving_els.each (i, el) =>
            $el = $(el)
            default_value = $el.data('default_value')
            $el.css(@_options.move_property, @_options.height + default_value)

    close: (e) =>
        e?.stopPropagation()
        @is_open = false
        $body.removeAttr('data-drawer_open')
        @_active_name = null
        @$el.css
            height: 0
        @_moving_els.each (i, el) =>
            $el = $(el)
            default_value = $el.data('default_value')
            $el.css(@_options.move_property, default_value)

    setContent: (content_name) ->
        @_active_name = content_name
        content_view = @_options.content[content_name]
        @$el.html(content_view.el)
        content_view.onShow?()


    toggleContent: (content_name) ->
        # if open and not active
        if content_name is @_active_name
            @close()
        else
            @open()
            @setContent(content_name)
        return @is_open



window.Drawer = Drawer