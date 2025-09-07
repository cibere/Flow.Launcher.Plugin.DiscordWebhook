# Flow.Launcher.Plugin.DiscordWebhook
 
Send messages through discord webhooks directly in flow.

## Usage

*Note: This "guide" assumes that your action keyword is "dischook"*

### Sending a message to a url

```
dischook <url> <message>
```

### Adding a url as a preset

*Note: This result will only appear if the preset keyword does not contain any spaces*

```
dischook <url> <preset keyword>
```

### Sending a message to a preset

```
dischook <preset keyword> <message>
```

### Display all presets

```
dischook
```

### Deleting a preset

Find the result for the preset you want to delete, and press the `Remove Webhook` button in the result's context menu

```
dischook
```