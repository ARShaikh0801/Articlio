$path = 'c:\Users\A K Shaikh\Documents\Projects\Articlio Blog\templates\blog\blogPost.html'
$content = Get-Content -Raw -Encoding UTF8 $path
$content = $content.Replace('"Unlike <svg', '"<span class=''hidden sm:inline''>Unlike</span> <svg')
$content = $content.Replace('"Like <svg', '"<span class=''hidden sm:inline''>Like</span> <svg')
$content = $content.Replace('"Saved <svg', '"<span class=''hidden sm:inline''>Saved</span> <svg')
$content = $content.Replace('"Save <svg', '"<span class=''hidden sm:inline''>Save</span> <svg')
Set-Content -Path $path -Value $content -Encoding UTF8
Write-Output 'Replaced successfully'
