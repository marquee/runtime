console.log 'gallery.coffee'

$('[data-cover_type="gallery"]').each (i, el) ->
    $gallery = $(el)
    urls = JSON.parse($gallery.attr('data-cover_urls'))
    if urls.length > 0
        console.log urls, $gallery
        $prev_button = $('<button class"Gallery_prev_button">Prev</button>')
        $next_button = $('<button class"Gallery_next_button">Next</button>')
        $gallery.append($prev_button, $next_button)

        current_i = 0

        renderImage = ->
            console.log urls[current_i]
            $gallery.css
                'background-image': "url(#{ urls[current_i]['1280'] })"

        $prev_button.on 'click', ->
            current_i -= 1
            if current_i < 0
                current_i = urls.length - 1
            renderImage()

        $next_button.on 'click', ->
            current_i += 1
            if current_i is urls.length
                current_i = 0
            renderImage()