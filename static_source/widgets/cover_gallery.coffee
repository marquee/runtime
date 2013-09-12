console.log 'gallery.coffee'

# Two modes: static and slider. Static (default) simply replaces the images
# in-place. Slider transitions between the images by sliding them. To set the
# mode, set the `data-gallery_mode` on the cover el to `"static"` or `"slider"`.

class Gallery
    constructor: (el) ->
        @$el = $(el)
        @_urls = JSON.parse(@$el.attr('data-cover_urls'))
        @_mode = @$el.attr('data-gallery_mode')
        if not @_mode
            @_mode = 'static'
        @_current_i = 0

        if @_urls.length > 1
            @_configureEl()
            $(window).on('resize', @_configureEl)

    next: =>
        @_current_i += 1
        if @_current_i is @_urls.length
            @_current_i = 0
        @_transitionImage()

    previous: =>
        @_current_i -= 1
        if @_current_i < 0
            @_current_i = @_urls.length - 1
        @_transitionImage()

    _transitionImage: ->

        switch @_mode
            when 'static'
                @_transitionStatic()
            when 'slider'
                @_transitionSlider()

    _configureEl: =>
        switch @_mode
            when 'static'
                @_configureStatic()
            when 'slider'
                @_configureSlider()
        @_setUpButtons()
        @$el.addClass("Gallery-#{ @_mode }")

    _setUpButtons: ->
        if not @_$prev_button
            @_$prev_button = $('<button class="Gallery_button Gallery_button-prev">Prev</button>')
            @_$next_button = $('<button class="Gallery_button Gallery_button-next">Next</button>')
            @$el.append(@_$prev_button, @_$next_button)
            @_$prev_button.on('click', @previous)
            @_$next_button.on('click', @next)
        # Defer so the buttons have height
        setTimeout =>
            top = (@$el.height() - @_$prev_button.height()) / 2
            @_$prev_button.css
                top: top
            @_$next_button.css
                top: top



    _configureStatic: ->
    _transitionStatic: ->
        console.log '_transitionStatic', @_urls, @_current_i
        @$el.css
            'background-image': "url(#{ @_urls[@_current_i]['1280'] })"


    _configureSlider: ->
        @$el.css('background-image': '')

        if not @_$slider?
            @_$slider = $('<div class="Gallery_slider"></div>')
            @$el.append(@_$slider)
        @_$slider.empty()

        width = @$el.width()
        height = @$el.height()

        @_$slider.css
            height: height
            width: width * @_urls.length
            left: width * 0.1
        $.each @_urls, (i, img) =>
            $image = $('<div class="Gallery_image"></div>')
            $image.css
                'background-image': "url(#{ img['1280'] })"
                width: width * 0.75
                height: height * 0.75
                top: height * 0.1
                left: i * width * 0.8
            @_$slider.append($image)
        @_transitionSlider()
        

    _transitionSlider: ->
        width = @$el.width()
        console.log 'new left', width * 0.1 + width * 0.8 * @_current_i
        @_$slider.css
            left: width * 0.1 - width * 0.8 * @_current_i
        @_$slider.find('.Gallery_image[data-active]').removeAttr('data-active')
        console.log $(@_$slider.find('.Gallery_image')[@_current_i])
        $(@_$slider.find('.Gallery_image')[@_current_i]).attr('data-active', true)


$('[data-cover_type="gallery"]').each (i, el) -> new Gallery(el)

